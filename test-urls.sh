urls="
https://www.apple.com 
https://www.dropbox.com 
https://facebook.com 
https://www.flickr.com 
https://foursquare.com 
https://github.com 
https://google.com 
http://google.com 
http://instagram.com 
https://www.linkedin.com 
https://www.reddit.com 
https://soundcloud.com 
https://stackoverflow.com 
http://store.steampowered.com 
https://www.tumblr.com 
https://twitter.com 
"
for url in $urls; do
    echo $url
    curl --user derp:herp --data "url=$url" https://page-watch.com/c 2>/dev/null | jq . | grep hid
    sleep 1
done
