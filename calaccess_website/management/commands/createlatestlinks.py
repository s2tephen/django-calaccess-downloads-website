#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Save copies of data files from the most recently completed update in a latest/
directory in the Django project's default file storage.
"""
import os
import re
import logging
from django.conf import settings
import boto3
from calaccess_raw.models import RawDataVersion
from django.core.management.base import BaseCommand
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Save copies of data files from the most recently completed update in a latest/
    directory in the Django project's default file storage.
    """
    help = "Save copies of data files from the most recently completed update\
in a latest directory in the Django project's default file storage."

    def handle(self, *args, **options):
        # set up boto session
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        # and client
        self.client = self.session.client('s3')

        # get the version of last update that finished
        v = RawDataVersion.objects.latest('update_finish_datetime')

        logger.debug(
            'Copying files for {:%m-%d-%Y %H:%M:%S} version to latest/'.format(
                v.release_datetime
            )
        )

        # save downloaded zip to the latest dir
        if v.download_zip_archive:
            # strip the datetime from the zip name
            zip_name = self.strip_datetime(
                os.path.basename(v.download_zip_archive.name),
            )
            self.copy_to_latest(
                v.clean_zip_archive.name,
                self.get_latest_path(zip_name),
            )
        # save cleaned zip to the latest dir
        if v.clean_zip_archive:
            # strip the datetime from the zip name
            zip_name = self.strip_datetime(
                os.path.basename(v.clean_zip_archive.name),
            )
            self.copy_to_latest(
                v.clean_zip_archive.name,
                self.get_latest_path(zip_name),
            )

        # loop through all of the raw data files
        for f in v.files.all():
            # save downloaded file to the latest directory
            self.copy_to_latest(
                f.download_file_archive.name,
                self.get_latest_path(f.download_file_archive.name)
            )

            if f.clean_file_archive:
                # save cleaned file to the latest directory
                self.copy_to_latest(
                    f.clean_file_archive.name,
                    self.get_latest_path(f.clean_file_archive.name)
                )

            if f.error_log_archive:
                # save error log file to the latest directory
                self.copy_to_latest(
                    f.error_log_archive.name,
                    self.get_latest_path(f.error_log_archive.name)
                )

    def get_latest_path(self, old_path):
        """
        Convert the file path to a latest file path
        """
        base_name = os.path.basename(old_path)
        return os.path.join("latest", base_name)

    def copy_to_latest(self, source, target):
        """
        Copies the provided source key to the provided target key
        """
        logger.debug('Saving copy of %s' % os.path.basename(source))
        self.client.copy_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=target,
            CopySource={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': source,
            },
        )

    def strip_datetime(self, filename):
        """
        Removes the datetime portion from filename.
        """
        return re.sub(
            r'\d{2}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}',
            '',
            filename,
        )