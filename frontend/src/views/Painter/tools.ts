import { ILoadUrls } from "@/models/dataType";
type ITemp = {
  name: string;
  masked: boolean;
};

export function findCurrentCase(caseDetail: ITemp[], currentCaseName: string) {
  const result = caseDetail.filter((item) => {
    return item.name === currentCaseName;
  });
  return result[0];
}

export function revokeAppUrls(revokeUrls: ILoadUrls) {
  for (let key in revokeUrls) {
    const jsonUrl = revokeUrls[key].jsonUrl;
    const urls = revokeUrls[key].nrrdUrls as Array<string>;
    urls.forEach((url) => {
      URL.revokeObjectURL(url);
    });
    URL.revokeObjectURL(jsonUrl);
  }
}
