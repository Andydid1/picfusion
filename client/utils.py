def euclidean_dis(lhs_1, lhs_2, rhs_1, rhs_2):
  return (rhs_1 - lhs_1) ** 2 + (rhs_2 - lhs_2) ** 2 

def sort_by_geo(asset_lst, target_lati, target_long, order):
  dis_lst = [(euclidean_dis(asset.latitude, asset.longitude, target_lati, target_long), asset) for asset in asset_lst]
  sorted_lst = sorted(dis_lst, key=lambda x: x[0], reverse=order)
  return [x[1] for x in sorted_lst]

# asset1 = Asset()
# asset1.latitude = 1.01
# asset1.longitude = 1.02

# asset2 = Asset()
# asset2.latitude = 0.0
# asset2.longitude = 0.1

# asset3 = Asset()
# asset3.latitude = -1.3
# asset3.longitude = -2

# asset_lst = [asset1, asset2, asset3]
# for a in sort_by_geo(asset_lst, -100, -100):
#   print(a.latitude, a.longitude)