#!/bin/bash

# Variables
URL="https://sourceforge.net/projects/gmat/files/GMAT/GMAT-R2022a/gmat-ubuntu-x64-R2022a.tar.gz/download"
FILE_NAME="gmat"
CURRENT_DIR=$(pwd)
GMAT_DIR=${CURRENT_DIR}"/GMAT/R2022a"
GMAT_API_DIR=${GMAT_DIR}"/api"
GMAT_BIN_DIR=${GMAT_DIR}"/bin"

# Download the tar.gz file
echo "[INFO] Downloading $URL..."
wget $URL -O ${FILE_NAME}

# Check if the file was downloaded successfully
if [ $? -ne 0 ]; then
  echo "[INFO] Failed to download the file. Exiting."
  exit 1
fi

# Extract the tar.gz file
echo "[INFO] Extracting ${FILE_NAME}..."
tar -xzf ${FILE_NAME}

# Clean up the tar.gz file
echo "[INFO] Cleaning up..."
rm ${FILE_NAME}

echo "[INFO] Exporting environment bin dir variable"
export PYTHONPATH=$PYTHONPATH:${GMAT_BIN_DIR}

echo ${GMAT_API_DIR}

pushd $GMAT_API_DIR

# Create the ../bin/api_startup_file.txt with absolute paths
echo "[INFO] Create absolute path api_startup_file"
python3 BuildApiStartupFile.py

# Substitute api absolute path in import module file
echo "[INFO] Change the path in load_gmat.py"
sed -i 's/<TopLevelGMATFolder>/${GMAT_DIR}/g' ${GMAT_API_DIR}/load_gmat.py

popd
# Copy this file to the root
echo "[INFO] Copying load_gmat to root"
cp ${GMAT_API_DIR}/load_gmat.py ./load_gmat.py

echo "[INFO] Installation complete."