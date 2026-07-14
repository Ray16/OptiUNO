* GAMS-model hs019.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
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
objcon.. obj =e= power(x('1') - 
10, 3) + 
power(x('2') - 
20, 3);


con1..power((x('2')) - 5, 2) + 
power((x('1')) - 6, 2) =l= 82.810000000000002;
con2..power((x('1')) - 5, 2) + 
power((x('2')) - 5, 2) =g= 100;
x.lo('1')=13;
x.up('1')=100;
x.lo('2')=-0;
x.up('2')=100;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


