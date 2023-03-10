import { type } from "os";

export interface INrrdCaseNames {
  names: string[];
  details: Array<IDetails>;
  [proName: string]: any;
}

export interface IDetails {
  name: string;
  masked: false;
}

export interface IExportMask {
  caseId?: number;
  sliceIndex?: number;
  dataFormat?: string;
  width?: number;
  height?: number;
  voxelSpacing?: number[];
  spaceOrigin?: number[];
  data?: number[];
  [proName: string]: any;
}

export interface IExportMasks {
  caseId: string;
  masks: Array<IExportMask>;
}

export interface IReplaceMask {
  caseId: string;
  sliceId: number;
  mask: number[];
}

export interface IParams {
  params: unknown;
  responseType?: string;
}

export interface ICaseUrls {
  nrrdUrls: Array<string>;
  jsonUrl?: string;
}

export interface ILoadUrls {
  [proName: string]: any;
}
