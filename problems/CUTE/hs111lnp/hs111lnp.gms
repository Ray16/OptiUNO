* GAMS-model hs111lnp.dag.gms written by dag2gams Converter at 29/03/2004 16:59:01
* University of Vienna
$offdigit;
 Set i/1*3/;
 Set j/1*10/;
 Equations objcon
con1
con2
con3
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= exp(x('1')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('1') - 
6.0890000000000004) + 
exp(x('2')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('2') - 
17.164000000000001) + 
exp(x('3')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('3') - 
34.054000000000002) + 
exp(x('4')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('4') - 
5.9139999999999997) + 
exp(x('5')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('5') - 
24.721) + 
exp(x('6')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('6') - 
14.986000000000001) + 
exp(x('7')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('7') - 
24.100000000000001) + 
exp(x('8')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('8') - 
10.708) + 
exp(x('9')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('9') - 
26.661999999999999) + 
exp(x('10')) * ((- log(exp(x('1')) + 
exp(x('2')) + 
exp(x('3')) + 
exp(x('4')) + 
exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) + 
exp(x('8')) + 
exp(x('9')) + 
exp(x('10')))) + 
x('10') - 
22.178999999999998);


con1.. exp(x('3')) + 
exp(x('7')) + 
exp(x('8')) + 
2 * exp(x('9')) + 
exp(x('10')) =e= 1;
con2.. exp(x('4')) + 
2 * exp(x('5')) + 
exp(x('6')) + 
exp(x('7')) =e= 1;
con3.. exp(x('1')) + 
2 * exp(x('2')) + 
2 * exp(x('3')) + 
exp(x('6')) + 
exp(x('10')) =e= 2;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


