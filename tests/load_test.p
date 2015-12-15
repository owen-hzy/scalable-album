set terminal png
set output "load_test.png"
set title "http://localhost:8081/auth/login"
set size 1,0.7
set grid y
set xlabel "request"
set ylabel "response time (ms)"
plot "login10.dat" using 9 smooth sbezier with lines title "concurrent:10","login50.dat" using 9 smooth sbezier with lines title "concurrent:50","login100.dat" using 9 smooth sbezier with lines title "concurrent:100"
