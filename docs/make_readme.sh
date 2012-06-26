cd build/text
cat index.txt usage.txt custom_tests.txt setup.txt settings.txt
sed ':a;N;$!ba;s/Contents.*Usage/Usage/g' -i readme.txt
mv readme.txt ../../../README
