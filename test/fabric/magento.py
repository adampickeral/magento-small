import re
from fabric.api import env, run, hide, task
from envassert import detect, file, port, process, service, user
from hot.utils.test import get_artifacts


def magento_is_responding():
    with hide('running', 'stdout'):
        wget_cmd = ("wget --quiet --output-document - "
                    "--header='Host: example.com' http://localhost/")
        homepage = run(wget_cmd)
        if re.search('Magento Demo Store', homepage):
            return True
        else:
            return False


@task
def check():
    env.platform_family = detect.detect()

    assert file.exists('/var/www/magento/.configured'), \
        '.configured did not exist'

    if env.platform_family == 'rhel':
        memcache_user = 'memcached'
        php_fpm_process_name = 'php-fpm'
        php_fpm_service_name = 'php-fpm'
    elif env.platform_family == 'debian':
        memcache_user = 'memcache'
        php_fpm_process_name = 'php5-fpm'
        php_fpm_service_name = 'php5-fpm'

    assert port.is_listening(80), 'port 80 is not listening'
    # assert port.is_listening(443), 'port 443 is not listenging'
    assert port.is_listening(3306), 'port 3306 is not listening'
    assert port.is_listening(9001), 'port 9001 is not listening'
    assert port.is_listening(11211), 'port 11211 is not listening'
    assert port.is_listening(11212), 'port 11212 is not listening'

    assert user.exists("magento"), 'magento user does not exist'

    assert process.is_up("nginx"), 'nginx is not running'
    assert process.is_up(php_fpm_process_name), \
        '{} is not running'.format(php_fpm_process_name)
    assert process.is_up("redis"), 'redis is not running'

    assert service.is_enabled("nginx"), 'nginx service not enabled'
    assert service.is_enabled("redis"), 'redis service not enabled'
    assert service.is_enabled(php_fpm_service_name), \
        '{} not enabled'.format(php_fpm_service_name)

    assert magento_is_responding(), 'Magento did not respond as expected.'


@task
def artifacts():
    env.platform_family = detect.detect()
    get_artifacts()