import * as Copper from "copper3d_visualisation";

addEventListener("message", (event) => {
  const data = event.data;

  // 在 Worker 中执行计算量大的代码
  const masks = restructData(
    data.masksData,
    data.len,
    data.width,
    data.height,
    data.voxelSpacing,
    data.spaceOrigin,
    data.msg
  );
  const len = data.len;
  const width = data.width;
  const height = data.height;
  const result = {
    masks,
    len,
    width,
    height,
  };
  // 发送计算结果到主线程
  postMessage(result);
});

function deepCopy(obj: any): unknown {
  if (obj === null || typeof obj !== "object") {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj);
  }

  if (obj instanceof Array) {
    let copiedArray = [];
    for (let i = 0; i < obj.length; i++) {
      copiedArray[i] = deepCopy(obj[i]);
    }
    return copiedArray;
  }

  if (obj instanceof Object) {
    let copiedObject: any = {};
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        copiedObject[key] = deepCopy(obj[key]);
      }
    }
    return copiedObject;
  }

  throw new Error("Unable to copy obj! Its type isn't supported.");
}

function pruningData(originArr: Copper.paintImageType[]) {
  let pruningArray = [];
  for (let i = 0; i < originArr.length; i++) {
    pruningArray.push(originArr[i].image.data);
  }
  return pruningArray;
}

function restructData(
  originArr: Copper.paintImageType[],
  len: number,
  width: number,
  height: number,
  voxelSpacing: number[],
  spaceOrigin: number[],
  msg: string
) {
  const reformatData = [];

  let start_c: unknown = new Date();
  for (let i = 0; i < len; i++) {
    let exportTemp = {
      sliceIndex: 0,
      dataFormat:
        "RGBA - Each successive 4-digit number forms a pixel point in data array",
      width,
      height,
      voxelSpacing,
      spaceOrigin,
      data: [],
    };

    exportTemp.sliceIndex = originArr[i].index;
    if (msg === "save") {
      const copiedArray = originArr[i].image.data.slice();
      (exportTemp as any).data = [...copiedArray];
    }

    reformatData.push(exportTemp);
  }

  return reformatData;
}

export { pruningData };
