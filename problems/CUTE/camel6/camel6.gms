* GAMS-model camel6.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set j/1*2/;
 Equations objcon
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 4 * power(x('1'), 2) - 
4 * power(x('2'), 2) + 
x('1') * x('2') - 
2.1000000000000001 * power(x('1'), 4) + 
4 * power(x('2'), 4) + 
0.33333333333333331 * power(x('1'), 6);


x.lo('1')=-3;
x.up('1')=3;
x.lo('2')=-1.5;
x.up('2')=1.5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


