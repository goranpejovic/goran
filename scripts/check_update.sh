#! /bin/sh

UPDATES=$(yum check-update --quiet | grep -v -e '^$')
UPDATES_COUNT=$(echo $UPDATES | wc -l)
MAILTO="goran@itn.me"
MAILFROM="sender@itn.me"

if [[ $UPDATES_COUNT -gt 1 ]]; then
echo "Hello,
We have ${UPDATES_COUNT} pending update(s) on $(hostname).

Here are pending updates:
$UPDATES" | mail -r $MAILFROM -s "Updates for $(hostname): ${UPDATES_COUNT}" $MAILTO
fi
