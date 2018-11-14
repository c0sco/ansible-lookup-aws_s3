#!/usr/bin/env python

# (c) 2018, Matt Stofko <matt@mjslabs.com>
# GNU General Public License v3.0+ (see LICENSE or
# https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This plugin can be run directly by specifying S3 URLs on the command
# line, e.g. aws_s3.py s3://my-bucket/test.txt s3://my-bucket/test2.txt
#

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import sys
import re

from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

try:
    import boto3
    import botocore
except ImportError:
    raise AnsibleError("The lookup aws_s3 requires boto3 and botocore")


DOCUMENTATION = """
    lookup: aws_s3
    author:
      -  Matt Stofko <matt@mjslabs.com>
    requirements:
      - boto3 and botocore libraries
      - boto profile with valid AWS credentials
    short_description: look up data from an AWS S3 object
    description:
      - Return the contents of an S3 object at a given URL. If more than one
        URL is specified, concatenate the contents of all URLs supplied.
    options:
      _terms:
        description: S3 URL to object
        required: True
      profile:
        description: Boto profile to use to connect to S3
        default: None (default profile)
"""

EXAMPLES = """
- name: read in yaml from S3
  debug:
    msg: "{{ lookup('aws_s3', 's3://my-bucket/file.yml', profile='staging') }}"
"""

RETURN = """
    _raw:
      description:
        - Concatenated contents of objects at given S3 URLs
"""


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        contents = []
        try:
            session = boto3.session.Session(
                profile_name=kwargs.get('profile', None))
        except botocore.exceptions.ProfileNotFound:
            raise AnsibleError("Could not find boto profile")
        s3 = session.resource('s3')
        for term in terms:
            bucket, prefix = self.parse_s3_url(term)
            if bucket is None or prefix is None:
                raise AnsibleError("Could not determine bucket and key from"
                                   "the supplied URL")
            try:
                s3_file = s3.Object(bucket, prefix).get()
                contents.append(s3_file['Body'].read())
            except botocore.exceptions.ClientError as ex:
                if ex.response['Error']['Code'] == 'NoSuchKey':
                    raise AnsibleError("Could not find key {0}".format(prefix))
                elif ex.response['Error']['Code'] == 'NoSuchBucket':
                    raise AnsibleError("Could not find bucket {0}"
                                       .format(bucket))
                elif ex.response['Error']['Code'] == 'InvalidAccessKeyId':
                    raise AnsibleError("Invalid AWS credentials supplied in"
                                       "boto profile")
                else:
                    raise AnsibleError("Unknown error occurred")
        return contents

    def parse_s3_url(self, url):
        match = re.search(r'^s3://([^\/]+)/?(.*)', url)
        if match and match.group(1) and match.group(2):
            return match.group(1), match.group(2)
        return None, None


def main():
    if len(sys.argv) < 2:
        print("Usage: {0} <s3 url> [s3 url, ...]"
              .format(os.path.basename(__file__)))
        return -1

    print(''.join(LookupModule().run(sys.argv[1:], None)))

    return 0


if __name__ == "__main__":
    sys.exit(main())
