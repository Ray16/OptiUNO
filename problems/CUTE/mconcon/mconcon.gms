* GAMS-model mconcon.dag.gms written by dag2gams Converter at 29/03/2004 16:59:06
* University of Vienna
$offdigit;
 Set i/1*11/;
 Set j/1*15/;
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
con10
con11
;
Variables x(j), obj;
* Objective function (to be minimized) 
objcon.. obj =e= -x('1') - 
x('2') - 
x('3') - 
x('4') - 
x('5') - 
x('6') - 
x('7');


con1.. -x('11') - 
x('15') =e= 0;
con2.. x('11') + 
x('13') =e= 0;
con3.. -x('10') - 
x('13') =e= 0;
con4.. -x('9') + 
x('10') =e= -1000;
con5.. x('9') - 
x('12') =e= 0;
con6.. -x('8') + 
x('12') =e= 0;
con7.. x('8') - 
x('14') =e= 0;
con8.. abs(x('1')) * x('1') - 
abs(x('2')) * x('2') - 
1.0375378562666177e-322 * x('8') =e= 0;
con9.. abs(x('3')) * x('3') - 
abs(x('4')) * x('4') - 
1.0375378562666177e-322 * x('9') =e= 0;
con10.. abs(x('4')) * x('4') - 
abs(x('5')) * x('5') - 
1.0375378562666177e-322 * x('10') =e= 0;
con11.. abs(x('6')) * x('6') - 
abs(x('7')) * x('7') - 
1.0375378562666177e-322 * x('11') =e= 0;
x.up('1')=914.73000000000002;
x.up('3')=904.73000000000002;
x.up('5')=904.73000000000002;
x.up('7')=914.73000000000002;
x.up('15')=400;
Model m/All/;
m.workspace = 32;
m.optfile = 1;options nlp=convert;
Solve m using nlp minimizing obj;
display x.l, obj.l;
  


