set terminal png
set output "home.png"
set title "http://localhost:8081/"
set size 1,0.7
set grid y
set xlabel "request"
set ylabel "response time (ms)"
plot "home10.dat" using 9 smooth sbezier with lines title "concurrent:10","home50.dat" using 9 smooth sbezier with lines title "concurrent:50","home100.dat" using 9 smooth sbezier with lines title "concurrent:100"
