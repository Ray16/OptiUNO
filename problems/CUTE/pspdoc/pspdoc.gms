* GAMS-model pspdoc.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set j/1*4/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= sqrt(power(x('1'), 2) + 
power(x('2') - 
x('3'), 2) + 
1) + 
sqrt(power(x('2'), 2) + 
power(x('3') - 
x('4'), 2) + 
1);


x.up('1')=-1;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


