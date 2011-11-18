from django.utils import unittest
from django.contrib.auth.models import User

from models import Author, Book, Publisher, Address, ComplexObject, SubComplexOne, SubComplexTwo

from dockit.forms import DocumentForm
from dockit.models import TemporaryDocument

class BookTestCase(unittest.TestCase):

    def test_monolithic(self):
        user = User.objects.create_user(username='test', email='z@z.com')
        addr = Address(street_1='10533 Reagan Rd', city='San Diego', postal_code='92126', country='US', region='CA')

        author = Author(user=user)
        author.save()

        publisher = Publisher(name='Books etc', address=addr)
        publisher.save()

        book = Book(title='Of Mice and Men', publisher=publisher)
        book.authors.append(author)
        book.save()
        book.tags.append('historical')
        book.save()

        book = Book.objects.get(book.get_id())
        assert 'historical' in book.tags
        self.assertEqual(book.title, 'Of Mice and Men')
        self.assertEqual(book.publisher.name, 'Books etc')
        self.assertEqual(book.publisher.address.city, 'San Diego')
        assert book.authors[0].user
        
        #test that modifying a nested schema is preserved
        publisher.address.street_2 = 'Apt 1'
        publisher.save()
        
        publisher = Publisher.objects.get(publisher.get_id())
        
        self.assertEqual(publisher.address.street_2, 'Apt 1')
        
        book = Book.objects.filter(tags='historical')[0]
        self.assertEqual(book.title, 'Of Mice and Men')
        
        self.assertEqual(Book.objects.filter(tags='fiction').count(), 0)
        
        self.assertEqual(publisher.dot_notation('address.country'), 'US')
        
        publisher.dot_notation_to_field('address')
        
        publisher.dot_notation_set_value('address.street_2', '# 1')
        self.assertEqual(publisher.address.street_2, '# 1')
        
        book.dot_notation_set_value('authors.0.internal_id', 'foo')
        self.assertEqual(book.authors[0].internal_id, 'foo')
    
    def test_admin(self):
        import admin

class DotNotationTestCase(unittest.TestCase):
    def test_dot_notation_set_value(self):
        addr1 = Address(street_1='10533 Reagan Rd', city='San Diego', postal_code='92126', country='US', region='CA')
        addr2 = Address(street_1='10533 Mesane Rd', city='San Diego', postal_code='92126', country='US', region='CA')
        co = ComplexObject(field1='field1', addresses=[addr1], main_address=addr1)
        co.save()
        co.dot_notation_set_value('addresses.1', addr2)
        self.assertEqual(co.addresses[1].street_1, addr2.street_1)
        
        co.dot_notation_set_value('addresses.1.region', 'CO')
        self.assertEqual(co.addresses[1].region, 'CO')
        co.save()
        
        co.dot_notation_set_value('addresses.1.extra_data.thirdpartyid', 'ABCDEF')
        self.assertEqual(co.addresses[1].extra_data['thirdpartyid'], 'ABCDEF')
        co.save()
        
        co.dot_notation_set_value('addresses.1.extra_data.complexdict', {'foo':'bar'})
        co.dot_notation_set_value('addresses.1.extra_data.complexdict.bar', 'foo')
        self.assertTrue('bar' in co.addresses[1].extra_data['complexdict'])
        self.assertEqual(co.addresses[1].extra_data['complexdict']['bar'], 'foo')
        co.save()
        
        co.dot_notation_set_value('addresses.1.extra_data.complexdict.inception', {'level2':{}})
        co.dot_notation_set_value('addresses.1.extra_data.complexdict.inception.level2.level3', True)
        self.assertEqual(co.addresses[1].extra_data['complexdict']['inception']['level2']['level3'], True)
        co.save()
        
        co.dot_notation_set_value('addresses.1.extra_data.complexdict.inception.partners', [])
        co.dot_notation_set_value('addresses.1.extra_data.complexdict.inception.partners.0', Author(internal_id='1'))
        co.dot_notation_set_value('addresses.1.extra_data.complexdict.inception.partners.1', Author(internal_id='2'))
        self.assertEqual(co.addresses[1].extra_data['complexdict']['inception']['partners'][0].internal_id, '1')
        co.save()
        
        co = ComplexObject.objects.get(co.get_id())
        self.assertEqual(co.addresses[1].extra_data['complexdict']['inception']['partners'][0].internal_id, '1')

class FormTestCase(unittest.TestCase):
    def test_form(self):
        class CustomDocumentForm(DocumentForm):
            class Meta:
                document = ComplexObject
        
        form = CustomDocumentForm(data={'field1':'hello'})
        self.assertTrue(form.is_valid(), str(form.errors))
        instance = form.save()
        self.assertEqual(instance.field1, 'hello')
        
        #TODO test file field
    
    def test_dotnotation_form(self):
        class CustomDocumentForm(DocumentForm):
            class Meta:
                document = ComplexObject
                dotpath = 'main_address'
        
        instance = ComplexObject(field1='field1')
        instance.save()
        data = {'street_1': '10533 Mesane Rd',
                'city': 'San Diego',
                'postal_code': '92126',
                'country': 'US',
                'region': 'CA',}
        form = CustomDocumentForm(data=data, instance=instance)
        self.assertTrue(form.is_valid(), str(form.errors))
        instance = form.save()
        self.assertEqual(instance.main_address.region, 'CA')
    
    def test_form_to_generic_document(self):
        class CustomDocumentForm(DocumentForm):
            class Meta:
                document = ComplexObject
        instance = TemporaryDocument(_primitive_data={'field1':'hello'})
        form = CustomDocumentForm(instance=instance, data={'field1':'hello2'})
        self.assertEqual(form.initial['field1'], 'hello')
        self.assertTrue(form.is_valid(), str(form.errors))
        instance = form.save()
        self.assertEqual(instance._primitive_data['field1'], 'hello2')
        self.assertTrue(isinstance(instance, TemporaryDocument))
        
        
        class CustomDocumentAddressForm(DocumentForm):
            class Meta:
                document = ComplexObject
                dotpath = 'main_address'
        
        data = {'street_1': '10533 Mesane Rd',
                'city': 'San Diego',
                'postal_code': '92126',
                'country': 'US',
                'region': 'CA',}
        form = CustomDocumentAddressForm(data=data, instance=instance)
        self.assertTrue(form.is_valid(), str(form.errors))
        instance = form.save()
        self.assertEqual(instance._primitive_data['main_address']['region'], 'CA', str(instance._primitive_data))
        self.assertTrue(isinstance(instance, TemporaryDocument))

