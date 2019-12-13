import LoopProjectFile as LPF
import sys

# Start Main function
# Sanity check arguments
if len(sys.argv) < 2:
    print("Usage: python run.py <filename>")
    quit()
else:
    filename = sys.argv[1]

# Create basic Loop Project and add extents for broken hill region
LPF.CreateBasic(filename)
geodes = [-31.90835,-31.863242,141.493799,141.546666]
utm = [54,'S',6469600,6474600,546700,551700]
depth = [1000,6000]
spacing = [100,100,100]
LPF.Set(filename,"extents",geodesic=geodes,utm=utm,depth=depth,spacing=spacing)

# Check new file is valid and report the version of the file
LPF.CheckFileValid(filename, True)
resp = LPF.Get(filename,"version")
if resp["errorFlag"]: print(resp["errorString"])
else: print(resp["value"])

# Report the extents of the new file
resp = LPF.Get(filename,"extents")
if resp["errorFlag"]: print(resp["errorString"])
else:
    extents = resp["value"]
    print("Geodesic:", extents["geodesic"])
    print("UTM:     ", extents["utm"])
    print("Depth:   ", extents["depth"])
    print("Spacing: ", extents["spacing"])

# Grab the dummy dataset from the bh Loop Project File with shape (51x51x51)
# and add it to this project (required to have the same shape)
resp = LPF.Get("bh.loop3d","strModel")
if resp["errorFlag"]: print(resp["errorString"])
else:
    strData = resp["value"]
    resp2 = LPF.Set(filename,"strModel",data=strData,index=0)
    if resp2["errorFlag"]: print(resp2["errorString"])
    else: print("Data saved in new file")
    resp3 = LPF.Get(filename,"strModel",index=0)
    if resp3["errorFlag"]: print(resp3["errorString"])
    else: print("Data received again")
