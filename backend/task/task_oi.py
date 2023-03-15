from utils import convert_to_nii_sigel_channel, tools,convert

def json_to_nii(casename):
    tools.save()
    # Performing time-consuming calculation tasks
    convert_to_nii_sigel_channel(casename)
    # convert.convert_to_nii_full_channels(casename)