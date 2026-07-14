* GAMS-model haifas.dag.gms written by dag2gams Converter at 29/03/2004 17:00:0
* University of Vienna
$offdigit;
 Set i/1*9/;
 Set j/1*7/;
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
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= x('7');


con1..x('4') + 
x('7') - 
5 * power(x('3'), 2) =g= 0;
con2..x('4') + 
x('7') - 
5 * power(x('1'), 2) =g= 0;
con3..x('4') + 
x('7') - 
3.2000000000000002 * power(x('2'), 2) - 
0.80000000000000004 * power(x('5'), 2) + 
3.2000000000000002 * x('2') * x('5') =g= 0;
con4..x('4') + 
x('7') - 
20 * power(x('5'), 2) - 
20 * power(x('6'), 2) + 
40 * x('5') * x('6') =g= 0;
con5..x('4') + 
x('7') - 
3.2000000000000002 * power(x('2'), 2) - 
0.80000000000000004 * power(x('5'), 2) - 
3.2000000000000002 * x('2') * x('5') =g= 0;
con6..x('4') + 
x('7') - 
3.2000000000000002 * power(x('3'), 2) - 
0.80000000000000004 * power(x('6'), 2) - 
3.2000000000000002 * x('3') * x('6') =g= 0;
con7..x('4') + 
x('7') - 
5 * power(x('2'), 2) =g= 0;
con8..x('4') + 
x('7') - 
3.2000000000000002 * power(x('1'), 2) - 
0.80000000000000004 * power(x('4'), 2) + 
3.2000000000000002 * x('1') * x('4') =g= 0;
con9..x('4') + 
x('7') - 
20 * power(x('5'), 2) - 
20 * power(x('4'), 2) + 
40 * x('4') * x('5') =g= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


