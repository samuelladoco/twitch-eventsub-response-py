echo Script starts.
echo

init=`cat ../Codes/ter/__init__.py`
ver=${init:15:5}
echo ---- ver=${ver}
echo

echo ---- pyinstaller
source ../Venvs/myvenv/Scripts/activate
pyinstaller --clean --onefile --noconsole --runtime-tmpdir=. --name twitch-eventsub-response-py ../Codes/main.py
echo

echo ---- copy
mkdir ./twitch-eventsub-response-py-v${ver}/
cp --force ./dist/twitch-eventsub-response-py.exe ../Codes/config.json5 ../LICENSE ../README.pdf ./twitch-eventsub-response-py-v${ver}
echo

echo ---- zip
powershell -c Compress-Archive -Path "./twitch-eventsub-response-py-v${ver}/*" -DestinationPath twitch-eventsub-response-py-v${ver}.zip
echo

echo ---- remove
rm --recursive ./build ./dist/ twitch-eventsub-response-py.spec ./twitch-eventsub-response-py-v${ver}/
echo

read -p "Press enter to finish."
echo
