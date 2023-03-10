<template>
  <div id="bg" ref="base_container">
    <div ref="intro">
      <Intro />
    </div>
    <div ref="c_gui" id="gui"></div>
    <div ref="nrrd_c" class="nrrd_c"></div>
    <NavBar
      :file-num="fileNum"
      :max="max"
      :immediate-slice-num="immediateSliceNum"
      :contrast-index="contrastNum"
      :init-slice-index="initSliceIndex"
      @on-slice-change="getSliceChangedNum"
      @reset-main-area-size="resetMainAreaSize"
      @on-change-orientation="resetSlicesOrientation"
      @on-save="onSaveMask"
      @on-open-dialog="onOpenDialog"
    ></NavBar>
    <Upload
      :dialog="dialog"
      @on-close-dialog="onCloseDialog"
      @get-load-files-urls="readyToLoad"
    ></Upload>
  </div>
  <div>
    <Logo />
    <Bottom />
  </div>
</template>
<script setup lang="ts">
import { GUI } from "dat.gui";
import * as Copper from "copper3d_visualisation";
import "copper3d_visualisation/dist/css/style.css";
import Intro from "./components/intro.vue";
import Bottom from "./components/bottom.vue";
import Logo from "../../components/logo.vue";
import NavBar from "@/components/NavBar.vue";
import Upload from "@/components/Upload.vue";
import { onMounted, ref, watchEffect } from "vue";
import { storeToRefs } from "pinia";
import {
  IExportMask,
  ICaseUrls,
  IReplaceMask,
  ILoadUrls,
} from "@/models/dataType";
import {
  useFileCountStore,
  useNrrdCaseUrlsStore,
  useInitMarksStore,
  useReplaceMarksStore,
  useSaveMasksStore,
  useMaskStore,
} from "@/store/pinia_store";
import { findCurrentCase, revokeAppUrls } from "./tools";

let appRenderer: Copper.copperRenderer;
let max = ref(0);
let immediateSliceNum = ref(0);
let contrastNum = ref(0);
let fileNum = ref(0);
let initSliceIndex = ref(0);
let dialog = ref(false);

let base_container = ref<HTMLDivElement>();
let intro = ref<HTMLDivElement>();
let c_gui = ref<HTMLDivElement>();
let nrrd_c = ref<HTMLDivElement>();

let scene: Copper.copperScene | undefined;
let pre_slices = ref();

let gui = new GUI({ width: 300, autoPlace: false });
let nrrdTools: Copper.nrrd_tools;
let loadBarMain: Copper.loadingBarType;
let loadingContainer: HTMLDivElement, progress: HTMLDivElement;
let allSlices: Array<any> = [];
let urls: Array<string> = [];
let loadedUrls: ILoadUrls = {};

let filesCount = ref(0);
let selectedContrastFolder: GUI;
let firstLoad = true;
let loadCases = true;

let timer: any;
let currentCaseId = "";

type selecedType = {
  [key: string]: boolean;
};

const { cases } = storeToRefs(useFileCountStore());
const { getFilesNames } = useFileCountStore();
const { caseUrls } = storeToRefs(useNrrdCaseUrlsStore());
const { getCaseFileUrls } = useNrrdCaseUrlsStore();
const { sendInitMask } = useInitMarksStore();
const { sendReplaceMask } = useReplaceMarksStore();
const { sendSaveMask } = useSaveMasksStore();
const { maskBackend } = storeToRefs(useMaskStore());
const { getMaskDataBackend } = useMaskStore();
// web worker for send masks to backend
const worker = new Worker(new URL("../../utils/worker.ts", import.meta.url), {
  type: "module",
});

onMounted(async () => {
  await getInitData();
  c_gui.value?.appendChild(gui.domElement);
  appRenderer = new Copper.copperRenderer(
    base_container.value as HTMLDivElement
  );

  nrrdTools = new Copper.nrrd_tools(nrrd_c.value as HTMLDivElement);

  loadBarMain = Copper.loading();

  loadingContainer = loadBarMain.loadingContainer;
  progress = loadBarMain.progress;

  (nrrd_c.value as HTMLDivElement).appendChild(loadBarMain.loadingContainer);

  document.addEventListener("keydown", (e) => {
    if (e.code === "KeyF") {
      Copper.fullScreenListenner(base_container.value as HTMLDivElement);
    }
  });

  setupGui();
  loadModel("nrrd_tools");
  appRenderer.animate();
});

async function getInitData() {
  await getFilesNames();
}

const readyToLoad = (urlsArray: Array<string>) => {
  fileNum.value = urlsArray.length;
  urls = urlsArray;
  if (urls.length > 0) loadAllNrrds(urls);
};

const onSaveMask = async (flag: boolean) => {
  if (flag) {
    switchAnimationStatus("flex", "Saving masks data, please wait......");
    await sendSaveMask(currentCaseId);
    switchAnimationStatus("none");
  }
};

const onOpenDialog = (flag: boolean) => {
  dialog.value = flag;
};
const onCloseDialog = (flag: boolean) => {
  dialog.value = flag;
};

const resetSlicesOrientation = (axis: "x" | "y" | "z") => {
  nrrdTools.setSliceOrientation(axis);
  max.value = nrrdTools.getMaxSliceNum()[1];
  const { currentIndex, contrastIndex } =
    nrrdTools.getCurrentSlicesNumAndContrastNum();
  immediateSliceNum.value = currentIndex;
  contrastNum.value = contrastIndex;
};
const getSliceChangedNum = (sliceNum: number) => {
  nrrdTools.setSliceMoving(sliceNum);
};
const resetMainAreaSize = (factor: number) => {
  nrrdTools.setMainAreaSize(factor);
};

worker.onmessage = async function (ev: MessageEvent) {
  const result = ev.data;
  const body = {
    caseId: currentCaseId,
    masks: result.masks as IExportMask[],
  };
  let start_c: unknown = new Date();
  await sendInitMask(body);
  let end_c: unknown = new Date();
  let timeDiff_c = (end_c as number) - (start_c as number);
  console.log(`axios send Time taken: ${timeDiff_c}ms`);
  console.log("send");
};

const sendInitMaskToBackend = () => {
  const masksData = nrrdTools.paintImages.z;
  const dimensions = nrrdTools.getCurrentImageDimension();
  const len = masksData.length;
  const width = dimensions[0];
  const height = dimensions[1];
  const voxelSpacing = nrrdTools.getVoxelSpacing();
  const spaceOrigin = nrrdTools.getSpaceOrigin();
  if (len > 0) {
    worker.postMessage({
      masksData,
      len,
      width,
      height,
      voxelSpacing,
      spaceOrigin,
      msg: "init",
    });
  }
};

const loadJsonMasks = (url: string) => {
  loadingContainer.style.display = "flex";
  progress.innerText = "Loading masks data......";

  const xhr = new XMLHttpRequest();
  xhr.open("GET", url, true);
  xhr.responseType = "json";
  xhr.onload = function () {
    if (xhr.status === 200) {
      const data = xhr.response;
      loadingContainer.style.display = "none";
      nrrdTools.setMasksData(data, loadBarMain);
    }
  };
  xhr.send();
};

const setMaskData = () => {
  if (loadedUrls[currentCaseId]) {
    if (cases.value) {
      const currentCaseDetail = findCurrentCase(
        cases.value.details,
        currentCaseId
      );
      if (currentCaseDetail.masked) {
        if (caseUrls.value)
          loadJsonMasks(loadedUrls[currentCaseId].jsonUrl as string);
      } else {
        sendInitMaskToBackend();
      }
    }
  }
  // if (cases.value) {
  //   const currentCaseDetail = findCurrentCase(
  //     cases.value.details,
  //     currentCaseId
  //   );
  //   if (currentCaseDetail.masked) {
  //     if (caseUrls.value) loadTestJsonMasks(caseUrls.value.jsonUrl as string);
  //   } else {
  //     sendMaskToBackend();
  //   }
  // }
};

const switchAnimationStatus = (status: "flex" | "none", text?: string) => {
  loadingContainer.style.display = status;
  !!text && (progress.innerText = text);
};

const getMaskData = async (
  image: ImageData,
  sliceId: number,
  width: number,
  height: number,
  clearAllFlag?: boolean
) => {
  const copyImage = image.data.slice();
  const mask = [...copyImage];
  const body: IReplaceMask = {
    caseId: currentCaseId,
    sliceId,
    mask,
  };
  if (clearAllFlag) {
    sendInitMaskToBackend();
  } else {
    await sendReplaceMask(body);
  }
};

watchEffect(() => {
  if (
    filesCount.value != 0 &&
    allSlices.length != 0 &&
    filesCount.value === urls.length
  ) {
    console.log("All files ready!");
    // if (!!timer) {
    //   clearInterval(timer);
    // }
    nrrdTools.clear();
    allSlices.sort((a: any, b: any) => {
      return a.order - b.order;
    });
    nrrdTools.setShowInMainArea(true);
    nrrdTools.setAllSlices(allSlices);
    initSliceIndex.value = nrrdTools.getCurrentSliceIndex();

    const getSliceNum = (index: number, contrastindex: number) => {
      immediateSliceNum.value = index;
      contrastNum.value = contrastindex;
    };

    if (firstLoad) {
      nrrdTools.drag({
        showNumber: true,
        getSliceNum,
      });
      nrrdTools.draw(scene as Copper.copperScene, gui, { getMaskData });
      scene?.addPreRenderCallbackFunction(nrrdTools.start);
      const state = {
        release: () => {
          revokeAppUrls(loadedUrls);
          loadedUrls = {};
        },
      };
      let opts = gui.addFolder("opts");
      opts.add(state, "release");
    } else {
      nrrdTools.redrawMianPreOnDisplayCanvas();
    }

    if (loadCases) {
      setMaskData();
    }

    max.value = nrrdTools.getMaxSliceNum()[1];
    setTimeout(() => {
      initSliceIndex.value = 0;
      filesCount.value = 0;
    }, 1000);
    firstLoad = false;
    loadCases = false;

    const selectedState: selecedType = {};

    for (let i = 0; i < allSlices.length; i++) {
      if (i == 0) {
        selectedState["pre"] = true;
      } else {
        const key = "contrast" + i;
        selectedState[key] = true;
      }
    }

    nrrdTools.removeGuiFolderChilden(selectedContrastFolder);
    for (let i = 0; i < allSlices.length; i++) {
      let name = "";
      i === 0 ? (name = "pre") : (name = "contrast" + i);
      selectedContrastFolder.add(selectedState, name).onChange((flag) => {
        if (flag) {
          fileNum.value += 1;
          nrrdTools.addSkip(i);
        } else {
          fileNum.value -= 1;
          nrrdTools.removeSkip(i);
        }
        const maxNum = nrrdTools.getMaxSliceNum()[1];
        if (maxNum) {
          max.value = maxNum;
          const { currentIndex, contrastIndex } =
            nrrdTools.getCurrentSlicesNumAndContrastNum();

          immediateSliceNum.value = currentIndex;
          contrastNum.value = contrastIndex + 1;
        }
      });
    }
  }
});

async function loadModel(name: string) {
  scene = appRenderer.getSceneByName(name) as Copper.copperScene;
  if (scene == undefined) {
    scene = appRenderer.createScene(name) as Copper.copperScene;

    if (scene) {
      appRenderer.setCurrentScene(scene);

      if (scene) {
        scene.loadViewUrl("/NRRD_Segmentation_Tool/nrrd_view.json");
      }
      Copper.setHDRFilePath("/NRRD_Segmentation_Tool/venice_sunset_1k.hdr");
      // scene.updateBackground("#18e5a7", "#ff00ff");
      scene.updateBackground("#8b6d96", "#18e5e5");
    }

    appRenderer.updateEnvironment();

    if ((cases.value?.names as string[]).length > 0) {
      if (cases.value?.names) {
        switchAnimationStatus("flex", "Prepare Nrrd files, please wait......");
        currentCaseId = cases.value?.names[0];
        await getCaseFileUrls(cases.value?.names[0]);
        if (caseUrls.value) {
          urls = caseUrls.value.nrrdUrls;
          // every time switch cases, we store it
          loadedUrls[currentCaseId] = caseUrls.value;
        }
        loadAllNrrds(urls);
      }
    }
  }
}

const loadAllNrrds = (urls: Array<string>) => {
  switchAnimationStatus("none");
  fileNum.value = urls.length;
  allSlices = [];
  const mainPreArea = (
    volume: any,
    nrrdMesh: Copper.nrrdMeshesType,
    nrrdSlices: Copper.nrrdSliceType
    // gui?: GUI
  ) => {
    const newNrrdSlice = Object.assign(nrrdSlices, { order: 0 });
    allSlices.push(newNrrdSlice);
    pre_slices.value = nrrdSlices;

    filesCount.value += 1;
  };
  scene?.loadNrrd(urls[0], loadBarMain, mainPreArea);

  for (let i = 1; i < urls.length; i++) {
    scene?.loadNrrd(
      urls[i],
      loadBarMain,
      (
        volume: any,
        nrrdMesh: Copper.nrrdMeshesType,
        nrrdSlices: Copper.nrrdSliceType
      ) => {
        const newNrrdSlice = Object.assign(nrrdSlices, { order: i });
        allSlices.push(newNrrdSlice);
        filesCount.value += 1;
      }
    );
  }
};

function setupGui() {
  const state = {
    introduction: true,
    showContrast: false,
    switchCase: cases.value?.names[0],
    release: () => {
      revokeAppUrls(loadedUrls);
    },
  };
  gui
    .add(state, "introduction")
    .name("Intro Panel")
    .onChange((flag) => {
      flag
        ? ((intro.value as HTMLDivElement).style.display = "flex")
        : ((intro.value as HTMLDivElement).style.display = "none");
    });

  gui
    .add(state, "switchCase", cases.value?.names as string[])
    .onChange(async (value) => {
      switchAnimationStatus("flex", "Saving masks data, please wait......");
      currentCaseId = value;
      await getInitData();
      if (loadedUrls[value]) {
        switchAnimationStatus(
          "flex",
          "Prepare and Loading masks data, please wait......"
        );
        URL.revokeObjectURL(loadedUrls[value].jsonUrl);
        await getMaskDataBackend(value);
        loadedUrls[value].jsonUrl = maskBackend.value;
        urls = loadedUrls[value].nrrdUrls;
      } else {
        switchAnimationStatus("flex", "Prepare Nrrd files, please wait......");
        await getCaseFileUrls(value);
        if (caseUrls.value) {
          urls = caseUrls.value.nrrdUrls;
          loadedUrls[currentCaseId] = caseUrls.value;
        }
      }
      readyToLoad(urls);
      loadCases = true;
    });

  selectedContrastFolder = gui.addFolder("select display contrast");
  // let opts = gui.addFolder("opts");
  // opts.add(state, "release");
}
</script>

<style>
#bg {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  /* border: 1px solid palevioletred; */
}
#gui {
  position: absolute;
  top: 1px;
  right: 0px;
  z-index: 100;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
.nrrd_c {
  position: fixed;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
.copper3d_sliceNumber {
  position: fixed !important;
  width: 300px;
  text-align: center;
  top: 5% !important;
  right: 1% !important;
  left: 0px !important;
  margin: 0 auto;
  border: 1px solid salmon;
  border-radius: 10px;
  padding: 5px;
  /* color: crimson; */
  font-size: 0.9em;
  font-weight: 700;
  color: rgba(26, 26, 26, 0.965);
  cursor: no-drop;
  transition: border-color 0.25s;
}
.copper3d_sliceNumber:hover {
  border-color: #eb4a05;
}
.copper3d_sliceNumber:focus,
.copper3d_sliceNumber:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}

.copper3D_scene_div {
  display: flex;
  justify-content: center;
  align-items: center;
}

.copper3D_loading_progress {
  color: darkgray !important;
  text-align: center;
  width: 60vw;
}
/* h3 {
  color: crimson;
}
.intro p {
  font-size: 0.8em;
  color: darkgray;
  width: 100%;
} */
</style>
