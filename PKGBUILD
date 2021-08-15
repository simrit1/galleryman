# Maintainer: 0xsapphir3 <0xsapphir3@gmail.com>
pkgname=galleryman
pkgver=0.1
pkgrel=1
provides=("galleryman")
conflicts=("galleryman")
pkgdesc="Gallery written in Python for managing your photos"
url="https://github.com/0xsapphir3/GalleryMan"
arch=("any")
license=("MIT")
depends=("python>=3.6" "python-setuptools" )
source=("git+https://github.com/0xsapphir3/GalleryMan.git")
md5sums=("SKIP")

pkgver()
{
  printf "9.6.4"
}

package()
{
  python GalleryMan/setup.py install --root="$pkgdir"
}
