* GAMS-model hs043.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*4/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-5) * x('1') - 
5 * x('2') - 
21 * x('3') + 
7 * x('4') + 
power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('4'), 2) + 
2 * power(x('3'), 2);


con1..2 * x('1') - 
x('2') - 
x('4') + 
2 * power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) =l= 5;
con2..-x('1') - 
x('4') + 
power(x('1'), 2) + 
2 * power(x('2'), 2) + 
2 * power(x('4'), 2) + 
power(x('3'), 2) =l= 10;
con3..x('1') - 
x('2') + 
x('3') - 
x('4') + 
power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('4'), 2) + 
power(x('3'), 2) =l= 8;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


