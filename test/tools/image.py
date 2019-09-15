from __future__ import print_function

from datetime import datetime
from pprint import pprint, pformat
from subprocess import check_output
from os import environ as env

from novaclient.exceptions import NotFound

from service import glance, nova



def upload(img_name=env['OS_IMG_NAME'], img_path=env['OS_IMG_FILE'], img_format=None):
    """
    Create the ``env['OS_IMG_NAME']``.
    If there is a same name image, we will delete it and upload a new one.

    :type img_format: str
    :param img_format: The format of image.
        If none is provided, we using the subfilename or raw.
    """
    img_list = list(glance.images.list())

    disk_format = img_format
    if not img_format:
        if len(img_path.split('.')) != 1:
            disk_format = img_path.split('.')[-1]
        else:
            disk_format = 'raw'

    img_args = {
        'name': img_name,
        'is_public': 'False',
        'disk_format': disk_format,
        'container_format': 'bare',
        'description': " | ".join([
                "uname: {0}".format(check_output(['uname', '-msKr']).strip('\n')),
                "installer: {0}".format(env['INSTALLER_REV']),
                "upload time: {0}".format(datetime.now()),
            ]),
    }

    try:
        img = nova.images.find(name=img_name)
        logger.info('Old image {name} <{id}> exists.'.format(name=img.name, id=img.id))
        logger.info('Delete old image {name} <{id}>'.format(name=img.name, id=img.id))
        glance.images.delete(img.id)
    except NotFound:
        pass


    img = glance.images.create(name=img_args['name'],
        public=img_args['is_public'],
        disk_format=img_args['disk_format'],
        container_format=img_args['container_format'],
        description=img_args['description'],
    )
    logger.debug('Image info: {0}'.format(pformat(img)))
    logger.info('Start upload image {name} <{id}>'.format(name=img.name, id=img.id))
    with open(img_path) as fimg:
        glance.images.upload(image_id=img.id, image_data=fimg)
    logger.info('Uploading of {name} <{id}> finished.'.format(name=img.name, id=img.id))



if __name__ == '__main__':
    import logging
    from sys import argv

    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG)

    try:
        upload(img_path=argv[1])
    except Exception as e:
        upload()
