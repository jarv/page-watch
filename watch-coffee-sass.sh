kill -9 $(pgrep coffee)
kill -9 $(pgrep sass)

coffee -o static/js -cw coffee/ &
sass --watch sass:static/css &
cd static/
python -m SimpleHTTPServer 5555
