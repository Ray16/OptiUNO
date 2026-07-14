* GAMS-model bt9.dag.gms written by dag2gams Converter at 29/03/2004 16:59:08
* University of Vienna
$offdigit;
 Set i/1*2/;
 Set j/1*4/;
 Equations objcon
con1
con2
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -(x('1'));


con1.. x('4') - 
power(x('2'), 2) - 
power(x('1'), 3) =e= 0;
con2.. -x('4') + 
power(x('1'), 2) - 
power(x('3'), 2) =e= 0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


