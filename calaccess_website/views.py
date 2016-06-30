import os
from django.http import Http404
from calaccess_raw import get_model_list
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from bakery.views import (
    BuildableArchiveIndexView,
    BuildableYearArchiveView,
    BuildableDetailView,
    BuildableListView,
    BuildableRedirectView,
)
from calaccess_raw.models.tracking import RawDataVersion, RawDataFile


#
# Version based archives
#

class VersionArchiveIndex(BuildableArchiveIndexView):
    """
    A list of the latest versions of CAL-ACCESS in our archive
    """
    model = RawDataVersion
    date_field = "release_datetime"
    template_name = "calaccess_website/version_archive.html"
    build_path = "index.html"


class VersionYearArchiveList(BuildableYearArchiveView):
    """
    A list of all versions of CAL-ACCESS in a given year
    """
    model = RawDataVersion
    date_field = "release_datetime"
    make_object_list = True
    template_name = "calaccess_website/version_archive_year.html"


class VersionDetail(BuildableDetailView):
    """
    A detail page with everything about an individual CAL-ACCESS version
    """
    model = RawDataVersion
    template_name = 'calaccess_website/version_detail.html'

    def get_url(self, obj):
        return reverse('version_detail', kwargs=dict(pk=obj.pk))


class LatestVersion(BuildableRedirectView):
    """
    Redirect to the detail page of the latest CAL-ACCESS version
    """
    build_path = "versions/latest/index.html"
    pattern_name = 'version_detail'

    def get_redirect_url(self, *args, **kwargs):
        try:
            obj = RawDataVersion.objects.latest('release_datetime')
        except RawDataVersion.DoesNotExist:
            raise Http404
        return reverse("version_detail", kwargs=dict(pk=obj.pk))


#
# Raw data file based archives
#

class RawDataFileList(BuildableListView):
    queryset = get_model_list()
    template_name = 'calaccess_website/raw_data_files_list.html'
    context_object_name = 'raw data files'


class RawDataFileDetail(BuildableDetailView):
    """
    A detail page with everything we know about the provided raw data file.
    """
    template_name = 'calaccess_website/rawdatafile_detail.html'

    def get_queryset(self):
        """
        Returns a list of the raw data files as a key dictionary
        with the URL slug as the keys.
        """
        return dict((slugify(m().db_table), m) for m in get_model_list())

    def set_kwargs(self, obj):
        self.kwargs = {
            'file_name': obj
        }

    def get_object(self):
        """
        Returns the file model from the CAL-ACCESS raw data app that
        matches the provided slug.

        Raises a 404 error if one is not found
        """
        key = self.kwargs['file_name']
        try:
            return self.get_queryset()[key.lower()]
        except KeyError:
            raise Http404

    def get_url(self, obj):
        return reverse('rawdatafile_detail', kwargs=dict(file_name=obj))

    def get_context_data(self, **kwargs):
        """
        Add some extra bits to the template's context
        """
        context = super(RawDataFileDetail, self).get_context_data(**kwargs)
        # Pull all previous versions of the provided file
        context['version_list'] = RawDataFile.objects.filter(
            file_name=self.kwargs['file_name'].upper()
        ).order_by('-version__release_datetime')
        return context
    
    def build_queryset(self):
        [self.build_object(o) for o in self.get_queryset()]
