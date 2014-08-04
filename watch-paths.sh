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
https://github.com/jarv/dotfiles/blob/master/README.md
https://github.com/jarv/test-repo/blob/master/README.md
https://github.com/jarv/test-repo/tree/master/foo
https://github.com/jarv/test-repo/blob/master/foo/1.txt
"

for url in $urls; do
    curl --data "url=$url" http://localhost/g
done

