adsabs-vagrant
==============

adsabs + vagrant + fabric + puppet = yay, bootstrapped beer machines!

## Quick start

After installing [Vagrant](http://vagrantup.com/), create and boot the VM:

	vagrant up

SSH to the VM:

	vagrant ssh

Initialize stuff:

    fab init

Run your app:

	fab run
