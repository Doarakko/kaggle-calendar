from kaggle.api.kaggle_api_extended import KaggleApi

api = KaggleApi()
api.authenticate()
# competitions_list = api.competitions_list(category='featured')
# for i in competitions_list:
#     print(i)

# for key in dir(competitions_list[0]):
#     print('{}: {}'.format(key, getattr(competitions_list[0], key)))


def get_kernels_list(competition_name=None):
    api = KaggleApi()
    api.authenticate()
    return api.kernels_list(competition=competition_name, sort_by='dateCreated')


def main():
    competition_name = 'elo-merchant-category-recommendation'
    kernels_list = get_kernels_list(competition_name)
    for key in dir(kernels_list[0]):
        print(key, ': ', getattr(kernels_list[0], key))
        #kernel_url = 'https://www.kaggle.com/' + getattr(kernels_list[0], i)


# main()
kernels_list = api.kernels_list(competition='elo-merchant-category-recommendation')
for key in dir(kernels_list[0]):
    print('{}: {}'.format(key, getattr(kernels_list[0], key)))
