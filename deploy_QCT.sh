PROJ_PATH=$1
# PROJ_PATH=/data4/common/IR/ENV18PM_sample/
for s in $(ls -d ${PROJ_PATH}*/); do cp -p QCT/* ${s}/; done

