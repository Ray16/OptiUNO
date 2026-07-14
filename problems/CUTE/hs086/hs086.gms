* GAMS-model hs086.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*10/;
 Set j/1*5/;
 Equations objcon
con1
con2
con3
con4
con5
con6
con7
con8
con9
con10
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-15) * x('1') - 
27 * x('2') - 
36 * x('3') - 
18 * x('4') - 
12 * x('5') + 
39 * power(x('2'), 2) + 
10 * power(x('3'), 2) + 
39 * power(x('4'), 2) + 
30 * power(x('5'), 2) + 
30 * power(x('1'), 2) - 
40 * x('1') * x('2') - 
20 * x('1') * x('3') + 
64 * x('1') * x('4') - 
20 * x('1') * x('5') - 
12 * x('2') * x('3') - 
62 * x('2') * x('4') + 
64 * x('2') * x('5') - 
12 * x('3') * x('4') - 
20 * x('3') * x('5') - 
40 * x('4') * x('5') + 
4 * power(x('1'), 3) + 
8 * power(x('2'), 3) + 
10 * power(x('3'), 3) + 
6 * power(x('4'), 3) + 
2 * power(x('5'), 3);


con1..x('1') + 
x('2') + 
x('3') + 
x('4') + 
x('5') =g= 1;
con2..x('1') + 
2 * x('2') + 
3 * x('3') + 
4 * x('4') + 
5 * x('5') =g= 5;
con3..-x('1') - 
2 * x('2') - 
3 * x('3') - 
2 * x('4') - 
x('5') =g= -60;
con4..-x('1') - 
x('2') - 
x('3') - 
x('4') - 
x('5') =g= -40;
con5..2 * x('1') - 
4 * x('3') =g= -1;
con6..(-9) * x('2') - 
2 * x('3') + 
x('4') - 
2.7999999999999998 * x('5') =g= -4;
con7..(-2) * x('2') - 
4 * x('4') - 
x('5') =g= -4;
con8..(-3.5) * x('1') + 
2 * x('3') =g= -0.25;
con9..(-2) * x('2') + 
4 * x('4') + 
2 * x('5') =g= -2;
con10..(-16) * x('1') + 
2 * x('2') + 
x('4') =g= -40;
x.lo('1')=0;
x.lo('2')=0;
x.lo('3')=0;
x.lo('4')=0;
x.lo('5')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


