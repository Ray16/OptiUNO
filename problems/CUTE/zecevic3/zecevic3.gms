* GAMS-model zecevic3.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*2/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= (-84) * x('1') - 
24 * x('2') + 
7 * power(x('1'), 2) + 
3 * power(x('2'), 2) + 300;


con1..power(x('1'), 2) + 
power(x('2'), 2) =l= 9;
con2..x('1') * x('2') =g= 1;
x.lo('1')=-0;
x.up('1')=10;
x.lo('2')=-0;
x.up('2')=10;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


