* GAMS-model hs113.dag.gms written by dag2gams Converter at 29/03/2004 16:59:02
* University of Vienna
$offdigit;
 Set i/1*8/;
 Set j/1*10/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-14) * x('1') - 
16 * x('2') + 
power(x('1'), 2) + 
power(x('2'), 2) + 
power((x('3')) - 10, 2) + 
power((x('4')) - 3, 2) + 
5 * power(x('8'), 2) + 
power((x('10')) - 7, 2) + 
2 * power((x('5')) - 10, 2) + 
4 * power((x('6')) - 5, 2) + 
2 * power((x('7')) - 1, 2) + 
7 * power((x('9')) - 11, 2) + 
x('1') * x('2') + 45;


con1..8 * x('1') - 
2 * x('2') - 
5 * x('5') + 
2 * x('10') =g= -12;
con2..(-10) * x('1') + 
8 * x('2') + 
17 * x('8') - 
2 * x('9') =g= 0;
con3..(-4) * x('1') - 
5 * x('2') + 
3 * x('8') - 
9 * x('9') =g= -105;
con4..3 * x('1') - 
6 * x('2') + 
7 * x('10') - 
12 * power((x('5')) - 8, 2) =g= 0;
con5..(-14) * x('4') + 
6 * x('7') - 
power(x('1'), 2) - 
2 * power((x('2')) - 2, 2) + 
2 * x('1') * x('2') =g= 0;
con6..x('7') - 
3 * power(x('4'), 2) - 
0.5 * power((x('1')) - 8, 2) - 
2 * power((x('2')) - 4, 2) =g= -30;
con7..(-8) * x('2') + 
2 * x('6') - 
5 * power(x('1'), 2) - 
power((x('3')) - 6, 2) =g= -40;
con8..7 * x('6') - 
2 * power(x('3'), 2) - 
3 * power((x('1')) - 2, 2) - 
4 * power((x('2')) - 3, 2) =g= -120;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


