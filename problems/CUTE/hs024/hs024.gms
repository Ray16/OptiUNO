* GAMS-model hs024.dag.gms written by dag2gams Converter at 29/03/2004 16:53:53
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*2/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= 0.021383343303319476*((power((x('1')) - 3, 2) - 
9) * power(x('2'), 3));


con1..-x('1') - 
1.7320508075688772 * x('2') =g= -6;
con2..x('1') + 
1.7320508075688772 * x('2') =g= 0;
con3..0.57735026918962584 * x('1') - 
x('2') =g= 0;
x.lo('1')=0;
x.lo('2')=0;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


