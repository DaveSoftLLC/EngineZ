from random import*
storm_pos = []
storm_rad = [6000,4000,3000,2000,1000,500]
for a in range(len(storm_rad)):
            if storm_rad[a] == 6000:
                storm_pos.append([6000,4000])
            else:
                x = randint(storm_pos[a-1][0]-(storm_rad[a-1]-storm_rad[a])+200,storm_pos[a-1][0]+(storm_rad[a-1]-storm_rad[a])-200)
                y = randint(storm_pos[a-1][1]-(storm_rad[a-1]-storm_rad[a])+200,storm_pos[a-1][1]+(storm_rad[a-1]-storm_rad[a])-200)
                storm_pos.append([x,y])
print(storm_pos)
