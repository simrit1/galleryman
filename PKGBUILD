# Maintainer: 0xsapphir3 <0xsapphir3@gmail.com>
pkgname=GalleryMan
pkgver=0.1
pkgrel=1
provides=("galleryman")
conflicts=("galleryman")
pkgdesc="Gallery written in Python for managing your photos"
url="https://github.com/0xsapphir3/GalleryMan"
arch=("any")
license=("MIT")
depends=("python>=3.6" "python-setuptools" "wget")
source=("git+https://github.com/0xsapphir3/GalleryMan.git")
md5sums=("SKIP")

_gitname="galleryman"

pkgver() {
  wget https://raw.githubusercontent.com/0xsapphir3/GalleryMan/main/GalleryMan/__version__.txt
  cat __version__.txt
}

build() {
  cd "${srcdir}/${pkgname}"
  python setup.py build
}

package() {
  cd "${srcdir}/${pkgname}"
  python3 setup.py install --root="$pkgdir" --optimize=1 || return 1
}