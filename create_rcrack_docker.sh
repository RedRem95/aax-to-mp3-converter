
unzip Audible_Tables.zip || exit
rm Audible_Tables.zip
SWD=$(pwd)
cd /tmp || exit
git clone https://github.com/inAudible-NG/RainbowCrack-NG.git RainbowCrack || exit
cd RainbowCrack/src || exit
make -f Makefile || exit
cp rcrack "${SWD}/rcrack"
cd /tmp || exit
rm -r RainbowCrack

cd ${SWD} || exit