# Copy this script to Proj folder and run it
# Proj=CBDPI_CBD
# Proj=ENV18PM
# Code_Path=/data1/inqlee0704/IR/IR_python/INEX
Proj=$1
# Code_Path=$2
for s in $(ls -d ${Proj}*/); do cp -p * ${s}/; done

