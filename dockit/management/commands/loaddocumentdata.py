import sys
import os
import gzip
import zipfile
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.db.models import get_apps
from django.utils.itercompat import product

from dockit.core import serializers

try:
    import bz2
    has_bz2 = True
except ImportError:
    has_bz2 = False

class Command(BaseCommand):
    help = 'Installs the named fixture(s) in the database.'
    args = "fixture [fixture ...]"

    def handle(self, *fixture_labels, **options):
        self.style = no_style()

        verbosity = int(options.get('verbosity', 1))
        show_traceback = options.get('traceback', False)
        
        # Keep a count of the installed objects and fixtures
        fixture_count = 0
        loaded_object_count = 0
        fixture_object_count = 0
        models = set()

        humanize = lambda dirname: dirname and "'%s'" % dirname or 'absolute path'
        
        class SingleZipReader(zipfile.ZipFile):
            def __init__(self, *args, **kwargs):
                zipfile.ZipFile.__init__(self, *args, **kwargs)
                if settings.DEBUG:
                    assert len(self.namelist()) == 1, "Zip-compressed fixtures must contain only one file."
            def read(self):
                return zipfile.ZipFile.read(self, self.namelist()[0])

        compression_types = {
            None:   file,
            'gz':   gzip.GzipFile,
            'zip':  SingleZipReader
        }
        if has_bz2:
            compression_types['bz2'] = bz2.BZ2File

        app_module_paths = []
        for app in get_apps():
            if hasattr(app, '__path__'):
                # It's a 'models/' subpackage
                for path in app.__path__:
                    app_module_paths.append(path)
            else:
                # It's a models.py module
                app_module_paths.append(app.__file__)

        app_fixtures = [os.path.join(os.path.dirname(path), 'fixtures') for path in app_module_paths]
        for fixture_label in fixture_labels:
            parts = fixture_label.split('.')

            if len(parts) > 1 and parts[-1] in compression_types:
                compression_formats = [parts[-1]]
                parts = parts[:-1]
            else:
                compression_formats = compression_types.keys()

            if len(parts) == 1:
                fixture_name = parts[0]
                formats = serializers.get_public_serializer_formats()
            else:
                fixture_name, format = '.'.join(parts[:-1]), parts[-1]
                if format in serializers.get_public_serializer_formats():
                    formats = [format]
                else:
                    formats = []

            if formats:
                if verbosity >= 2:
                    self.stdout.write("Loading '%s' fixtures...\n" % fixture_name)
            else:
                self.stderr.write(
                    self.style.ERROR("Problem installing fixture '%s': %s is not a known serialization format.\n" %
                        (fixture_name, format)))
                return

            if os.path.isabs(fixture_name):
                fixture_dirs = [fixture_name]
            else:
                fixture_dirs = app_fixtures + list(settings.FIXTURE_DIRS) + ['']

            for fixture_dir in fixture_dirs:
                if verbosity >= 2:
                    self.stdout.write("Checking %s for fixtures...\n" % humanize(fixture_dir))

                label_found = False
                for combo in product(formats, compression_formats):
                    format, compression_format = combo
                    file_name = '.'.join(
                        p for p in [
                            fixture_name, format, compression_format
                        ]
                        if p
                    )

                    if verbosity >= 3:
                        self.stdout.write("Trying %s for %s fixture '%s'...\n" % \
                            (humanize(fixture_dir), file_name, fixture_name))
                    full_path = os.path.join(fixture_dir, file_name)
                    open_method = compression_types[compression_format]
                    try:
                        fixture = open_method(full_path, 'r')
                        if label_found:
                            fixture.close()
                            self.stderr.write(self.style.ERROR("Multiple fixtures named '%s' in %s. Aborting.\n" %
                                (fixture_name, humanize(fixture_dir))))
                            return
                        else:
                            fixture_count += 1
                            objects_in_fixture = 0
                            loaded_objects_in_fixture = 0
                            if verbosity >= 2:
                                self.stdout.write("Installing %s fixture '%s' from %s.\n" % \
                                    (format, fixture_name, humanize(fixture_dir)))
                            try:
                                objects = serializers.deserialize(format, fixture)
                                for obj in objects:
                                    objects_in_fixture += 1
                                    
                                    loaded_objects_in_fixture += 1
                                    models.add(obj.object.__class__)
                                    obj.save()
                                loaded_object_count += loaded_objects_in_fixture
                                fixture_object_count += objects_in_fixture
                                label_found = True
                            except (SystemExit, KeyboardInterrupt):
                                raise
                            except Exception:
                                import traceback
                                fixture.close()
                                if show_traceback:
                                    traceback.print_exc()
                                else:
                                    self.stderr.write(
                                        self.style.ERROR("Problem installing fixture '%s': %s\n" %
                                             (full_path, ''.join(traceback.format_exception(sys.exc_type,
                                                 sys.exc_value, sys.exc_traceback)))))
                                return
                            fixture.close()

                            # If the fixture we loaded contains 0 objects, assume that an
                            # error was encountered during fixture loading.
                            if objects_in_fixture == 0:
                                self.stderr.write(
                                    self.style.ERROR("No fixture data found for '%s'. (File format may be invalid.)\n" %
                                        (fixture_name)))
                                return

                    except Exception, e:
                        if verbosity >= 2:
                            self.stdout.write("No %s fixture '%s' in %s.\n" % \
                                (format, fixture_name, humanize(fixture_dir)))

        
        if fixture_object_count == 0:
            if verbosity >= 1:
                self.stdout.write("No fixtures found.\n")
        else:
            if verbosity >= 1:
                if fixture_object_count == loaded_object_count:
                    self.stdout.write("Installed %d object(s) from %d fixture(s)\n" % (
                        loaded_object_count, fixture_count))
                else:
                    self.stdout.write("Installed %d object(s) (of %d) from %d fixture(s)\n" % (
                        loaded_object_count, fixture_object_count, fixture_count))

