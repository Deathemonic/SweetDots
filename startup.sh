FILE=/workspace/SweetDots/aliases.sh
FILE1=/workspace/SweetDots/startup.sh
if [ -f "$FILE" ]; then 
    clear && echo "aliases file exists."
else
    touch aliases.sh
    chmod +x aliases.sh
    curl https://gitlab.com/nstoc6696/Gitpod-VNC/-/raw/master/aliases.sh > aliases.sh
    rm README.md
fi
if [ -f "$FILE1" ]; then
    rm $FILE1
fi