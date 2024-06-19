# For non-docker related measurements
mkdir -p chrome_120

pushd "./chrome_120" > /dev/null

wget -q 'https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F1217362%2Fchrome-linux.zip?generation=1698717835110888&alt=media' -O ./chrome_120.zip && \
unzip chrome_120.zip && \
mv chrome-linux/* ./ && \
rm -rf chrome-linux chrome_120.zip

popd > /dev/null

# For docker measurements (performance)
pushd "./performance/docker/chrome" > /dev/null
mkdir data
chmod 777 data
popd > /dev/null
