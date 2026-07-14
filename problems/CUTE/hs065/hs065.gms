* GAMS-model hs065.dag.gms written by dag2gams Converter at 29/03/2004 16:58:58
* University of Vienna
$offdigit;
 Set i/1*1/;
 Set j/1*3/;
 Equations objcon
con1
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= power((x('3')) - 5, 2) + 
power(x('1') - 
x('2'), 2) + 
0.1111111111111111 * power(x('1') + 
x('2') - 
10, 2);


con1..power(x('1'), 2) + 
power(x('2'), 2) + 
power(x('3'), 2) =l= 48;
x.lo('3')=-5;
x.up('3')=5;
x.lo('1')=-4.5;
x.up('1')=4.5;
x.lo('2')=-4.5;
x.up('2')=4.5;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


