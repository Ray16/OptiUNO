* GAMS-model hs100.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*4/;
 Set j/1*7/;
 Equations objcon
con1
con2
con3
con4
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-10) * x('5') - 
8 * x('7') + 
power((x('1')) - 10, 2) + 
7 * power(x('5'), 2) + 
5 * power((x('2')) - 12, 2) + 
3 * power((x('4')) - 11, 2) - 
4 * x('5') * x('7') + 
power(x('3'), 4) + 
power(x('7'), 4) + 
10 * power(x('6'), 6);


con1..(-5) * x('5') + 
11 * x('7') - 
4 * power(x('1'), 2) - 
2 * power(x('3'), 2) - 
power(x('2'), 2) + 
3 * x('1') * x('2') =g= 0;
con2..23 * x('1') - 
8 * x('7') + 
6 * power(x('5'), 2) + 
power(x('2'), 2) =l= 196;
con3..7 * x('1') + 
3 * x('2') + 
x('4') - 
x('6') + 
10 * power(x('3'), 2) =l= 282;
con4..x('3') + 
5 * x('6') + 
2 * power(x('1'), 2) + 
4 * power(x('4'), 2) + 
3 * power(x('2'), 4) =l= 127;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


