import glob
import cv2

IMG_SIZE = {
    'height': 128,
    'width': 90,
    'channel': 3
}

from_path = './tools/raw_img/*.png'
to_folder = './tools/clipped_img/'

filelist = glob.glob(from_path)

for filename in filelist:
    img_name = filename.split('\\')[1]
    output_img_names = []
    
    img = cv2.imread(filename)

    height = img.shape[0]
    width = img.shape[1]
    channels = img.shape[2]

    # height == 289なら,800 // (90*289/128)で割れば個数
    num = round(width / (IMG_SIZE['width'] * height / IMG_SIZE['height']))
    
    print(num)

    # リサイズ
    scale = IMG_SIZE['height'] / height
    img = cv2.resize(img, dsize=None, fx=scale, fy=scale)

    cut_width = img.shape[1] // num + 1
    #if abs(cut_width - IMG_SIZE['width']) > 15:
    #    print('warning! size diff is big')

    # 1個1個保存
    if num == 1:
        output_img_names.append(34)
    elif num == 3:
        output_img_names.append(0)
        output_img_names.append(10)
        output_img_names.append(20)
    elif num == 4:
        output_img_name_base = 30
        for i in range(4):
            output_img_names.append(output_img_name_base+i)
    elif num == 9:
        if 'manzu' in img_name:
            output_img_name_base = 1
        elif 'pinzu' in img_name:
            output_img_name_base = 11
        elif 'souzu' in img_name:
            output_img_name_base = 21
        for i in range(9):
            output_img_names.append(output_img_name_base+i)
    
    if num == 1:
        cv2.imwrite(to_folder+img_name, img)
    else:
        for i in range(num):
            tiny_img = img[:, i*cut_width:(i+1)*cut_width, :]
            cv2.imwrite(to_folder+str(output_img_names[i])+'.png', tiny_img)