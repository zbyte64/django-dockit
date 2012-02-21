from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--format', default='json', dest='format',
            help='Specifies the output serialization format for fixtures.'),
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
    )
    help = ("Output the contents of the database as a fixture of the given "
            "format (using each model's default manager unless --all is "
            "specified).")
    #args = '[appname appname.ModelName ...]'

    def handle(self, *app_labels, **options):
        from dockit.schema.common import COLLECTIONS
        format = options.get('format','json')
        indent = options.get('indent',None)
        show_traceback = options.get('traceback', False)

        

        # Check that the serialization format exists; this is a shortcut to
        # avoid collating all the objects and _then_ failing.
        if format not in serializers.get_public_serializer_formats():
            raise CommandError("Unknown serialization format: %s" % format)

        try:
            serializers.get_serializer(format)
        except KeyError:
            raise CommandError("Unknown serialization format: %s" % format)

        # Now collate the objects to be serialized.
        objects = []
        excluded_documents = []
        for document in COLLECTIONS.itervalues():
            if document in excluded_documents:
                continue
            objects.extend(document.objects.all())

        try:
            return serializers.serialize(format, objects, indent=indent,
                        use_natural_keys=False)
        except Exception, e:
            if show_traceback:
                raise
            raise CommandError("Unable to serialize database: %s" % e)

