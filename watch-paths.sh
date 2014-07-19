set -x
urls="
www.github.com/edx/edx-platform
github.com/edx/edx-platform/tree/master/requirements/edx/sandbox
http://github.com/edx/edx-platform/tree/master/requirements/edx
https://github.com/edx/edx-platform/blob/master/CHANGELOG.rst
https://github.com/edx/edx-platform/tree/master/requirements
http://files.edx.org/vagrant-images/20140625-johnnycake-fullstack.box
https://github.com/path/to/invalid/file
http://github.com/path/to/invalid/file
https://google.com
http://google.com
"

for url in $urls; do
    curl --data "url=$url" http://localhost:8000/g
    sleep .1
done

