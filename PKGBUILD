# Maintainer: 0xsapphir3 <0xsapphir3@gmail.com>
pkgname=galleryman
pkgver=0.1
pkgrel=1
epoch=
pkgdesc="Gallery written in Python for managing your photos"
arch=(x86_64)
url="https://github.com/0xsapphir3/GalleryMan.git"
license=('MIT')
groups=()
depends=(python-setuptools)
makedepends=(python-setuptools)
checkdepends=()
optdepends=()
provides=()
conflicts=()
replaces=()
backup=()
options=()
install=
changelog=
source=("git+$url")
noextract=()
md5sums=("SKIP")
validpgpkeys=()


build() {
	python3 setup.py build
}


package() {
	python3 setup.py install --root="$pkgdir" --optimize=1 
}
