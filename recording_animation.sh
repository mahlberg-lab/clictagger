[ -f alice.txt ] || wget https://raw.githubusercontent.com/birmingham-ccr/corpora/80d00e4/ChiLit/alice.txt

echo "===== Type this into the recorded prompt"
cat <<EOF
# Tag alice.txt, see colourful output
clictagger alice.txt

# Output all suspensions in alice.txt into alice.csv
clictagger --csv alice.csv alice.txt quote.suspension.short quote.suspension.long
head alice.csv

# Start a webserver to view the tagged version of alice.txt
# Every reload of the page will re-read alice.txt
clictagger --serve alice.txt

# For more information, see --help
clictagger --help
EOF
echo "========================================"

PATH="./bin/$PATH:$PATH" PROMPT_COMMAND="" termtosvg \
    commandline_example.svg \
    -c "/bin/bash --noprofile -l" \
    -g 80x20
