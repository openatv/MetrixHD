for f in *.png; do
  convert "$f" -channel RGB -negate +channel "${f%.png}_neg.png"
  convert "${f%.png}_neg.png" -background white -alpha remove "${f%.png}.pbm"
  potrace -s -o "${f%.png}.svg" "${f%.png}.pbm"
  rm "${f%.png}_neg.png" "${f%.png}.pbm"
done

