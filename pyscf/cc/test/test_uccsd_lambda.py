import unittest
from pyscf import ao2mo
import numpy
import numpy as np
from pyscf import lib
from pyscf import gto
from pyscf import scf
from pyscf.cc import uccsd
from pyscf.cc import addons
from pyscf.cc import uccsd_lambda_slow as uccsd_lambda

mol = gto.Mole()
mol.atom = [
    [8 , (0. , 0.     , 0.)],
    [1 , (0. , -0.757 , 0.587)],
    [1 , (0. , 0.757  , 0.587)]]
mol.basis = '631g'
mol.spin = 2
mol.build()

class ccsd:
    def __init__(self,nso,nelec,h1e,int2e,h1e_is_fock=False):
        self.nso = nso
        self.nocc = nelec
        self.nvir = nso-nelec
        self.t1 = None
        self.t2 = None
        self.tau = None
        self.tau_tilde = None
        self.L1 = None
        self.L2 = None
        self.rspdm1 = None

        self.fock = h1e.copy()

        if h1e_is_fock is False:
            for p in range(self.nso):
                for q in range(self.nso):
                    for i in range(self.nocc):
                        self.fock[p,q] += int2e[p,i,q,i]

        self.f_oo = self.fock[:self.nocc,:self.nocc]
        self.f_ov = self.fock[:self.nocc,self.nocc:]
        self.f_vo = self.fock[self.nocc:,:self.nocc]
        self.f_vv = self.fock[self.nocc:,self.nocc:]
        self.w_oooo = int2e[:self.nocc,:self.nocc,:self.nocc,:self.nocc]
        self.w_ooov = int2e[:self.nocc,:self.nocc,:self.nocc,self.nocc:]
        self.w_oovo = int2e[:self.nocc,:self.nocc,self.nocc:,:self.nocc]
        self.w_ovoo = int2e[:self.nocc,self.nocc:,:self.nocc,:self.nocc]
        self.w_vooo = int2e[self.nocc:,:self.nocc,:self.nocc,:self.nocc]
        self.w_oovv = int2e[:self.nocc,:self.nocc,self.nocc:,self.nocc:]
        self.w_vvoo = int2e[self.nocc:,self.nocc:,:self.nocc,:self.nocc]
        self.w_ovov = int2e[:self.nocc,self.nocc:,:self.nocc,self.nocc:]
        self.w_ovvo = int2e[:self.nocc,self.nocc:,self.nocc:,:self.nocc]
        self.w_vovo = int2e[self.nocc:,:self.nocc,self.nocc:,:self.nocc]
        self.w_ovvv = int2e[:self.nocc,self.nocc:,self.nocc:,self.nocc:]
        self.w_vovv = int2e[self.nocc:,:self.nocc,self.nocc:,self.nocc:]
        self.w_vvov = int2e[self.nocc:,self.nocc:,:self.nocc,self.nocc:]
        self.w_vvvo = int2e[self.nocc:,self.nocc:,self.nocc:,:self.nocc]
        self.w_vvvv = int2e[self.nocc:,self.nocc:,self.nocc:,self.nocc:]


def update_amps(res1,res2,cc):
    "compute lambda_ia/lambda_ijab updates based on perturbation quasi-Newton method"

    return L1new, L2new

def update_l1l2_sub(mycc, t1, t2, l1, l2):
    l1new  = mycc.f_ov.copy()
    l1new += np.einsum('jiba,jb->ia', mycc.w_oovv, t1)
    l1new += np.einsum('ib,ba->ia', l1, mycc.f_vv)
    l1new -= np.einsum('ja,ij->ia', l1, mycc.f_oo)
    l1new += np.einsum('jb,ibaj->ia', l1, mycc.w_ovvo)
    l1new -= np.einsum('ib,ja,jb->ia', l1, mycc.f_ov, t1)
    l1new -= np.einsum('ja,ib,jb->ia', l1, mycc.f_ov, t1)
    l1new += np.einsum('jc,ciba,jb->ia', l1, mycc.w_vovv, t1)
    l1new -= np.einsum('ic,cjba,jb->ia', l1, mycc.w_vovv, t1)
    l1new -= np.einsum('kb,jika,jb->ia', l1, mycc.w_ooov, t1)
    l1new += np.einsum('ka,jikb,jb->ia', l1, mycc.w_ooov, t1)
    l1new += np.einsum('kc  ,kica->ia', np.einsum('jb,jkbc->kc  ', l1, t2), mycc.w_oovv)
    l1new += np.einsum('jkic,jkca->ia', np.einsum('ib,jkbc->jkic', l1, t2), mycc.w_oovv) * .5
    l1new += np.einsum('akbc,kibc->ia', np.einsum('ja,jkbc->akbc', l1, t2), mycc.w_oovv) * .5
    l1new -= np.einsum('kb  ,kiba->ia', np.einsum('jc,kc,jb->kb  ', l1, t1, t1), mycc.w_oovv)
    l1new += np.einsum('ikjb,kjba->ia', np.einsum('ic,kc,jb->ikjb', l1, t1, t1), mycc.w_oovv)
    l1new += np.einsum('acjb,jicb->ia', np.einsum('ka,kc,jb->acjb', l1, t1, t1), mycc.w_oovv)
    l1new += np.einsum('jica,cj->ia', l2, np.einsum('cb,jb->cj', mycc.f_vv, t1))
    l1new -= np.einsum('kiba,kb->ia', l2, np.einsum('jk,jb->kb', mycc.f_oo, t1))
    l1new += np.einsum('jicd,cdja->ia', l2, np.einsum('cdba,jb->cdja', mycc.w_vvvv, t1)) * .5
    l1new += np.einsum('klba,bikl->ia', l2, np.einsum('jikl,jb->bikl', mycc.w_oooo, t1)) * .5
    l1new -= np.einsum('kicb,bcak->ia', l2, np.einsum('jcak,jb->bcak', mycc.w_ovvo, t1))

    l1new -= np.einsum('kjca,icjk->ia', l2, np.einsum('icbk,jb->icjk', mycc.w_ovvo, t1))
    l1new += np.einsum('kica,ck  ->ia', l2, np.einsum('jcbk,jb->ck  ', mycc.w_ovvo, t1))
    l1new += np.einsum('jiba,bj->ia', l2, mycc.f_vo)
    l1new -= np.einsum('jibc,bcaj->ia', l2, mycc.w_vvvo) * .5
    l1new += np.einsum('jkba,ibjk->ia', l2, mycc.w_ovoo) * .5
    l1new -= np.einsum('jibc,jabc->ia', l2, np.einsum('ka,jkbc->jabc', mycc.f_ov, t2)) * .5
    l1new -= np.einsum('jkba,jkbi->ia', l2, np.einsum('ic,jkbc->jkbi', mycc.f_ov, t2)) * .5
    l1new += np.einsum('jiba,jb  ->ia', l2, np.einsum('kc,jkbc->jb  ', mycc.f_ov, t2))
    l1new -= np.einsum('jica,jc->ia', l2, np.einsum('kb,kc,jb->jc', mycc.f_ov, t1, t1))
    l1new -= np.einsum('dc,dica->ia', np.einsum('jkdb,jkbc->dc', l2, t2), mycc.w_vovv) * .5
    l1new += np.einsum('jidb,dajb->ia', l2, np.einsum('dkca,jkbc->dajb', mycc.w_vovv, t2))
    l1new -= np.einsum('jkda,dijk->ia', l2, np.einsum('dibc,jkbc->dijk', mycc.w_vovv, t2)) * .25
    l1new += np.einsum('jida,jd->ia', l2, np.einsum('dkbc,jkbc->jd', mycc.w_vovv, t2)) * .5
    l1new += np.einsum('kila,lk->ia', mycc.w_ooov, np.einsum('ljbc,jkbc->lk', l2, t2)) * .5
    l1new += np.einsum('libc,labc->ia', l2, np.einsum('jkla,jkbc->labc', mycc.w_ooov, t2)) * .25
    l1new -= np.einsum('ljba,iljb->ia', l2, np.einsum('kilc,jkbc->iljb', mycc.w_ooov, t2))
    l1new -= np.einsum('liba,lb  ->ia', l2, np.einsum('jklc,jkbc->lb  ', mycc.w_ooov, t2)) * .5
    l1new -= np.einsum('jidc,dcja->ia', l2, np.einsum('dkba,kc,jb->dcja', mycc.w_vovv, t1, t1))
    l1new -= np.einsum('kjda,dikj->ia', l2, np.einsum('dicb,kc,jb->dikj', mycc.w_vovv, t1, t1)) * .5
    l1new += np.einsum('kida,dk  ->ia', l2, np.einsum('djcb,kc,jb->dk  ', mycc.w_vovv, t1, t1))
    l1new += np.einsum('licb,cbla->ia', l2, np.einsum('kjla,kc,jb->cbla', mycc.w_ooov, t1, t1)) * .5

    l1new += np.einsum('ljca,cilj->ia', l2, np.einsum('kilb,kc,jb->cilj', mycc.w_ooov, t1, t1))
    l1new -= np.einsum('lica,cl  ->ia', l2, np.einsum('kjlb,kc,jb->cl  ', mycc.w_ooov, t1, t1))
    l1new -= np.einsum('jl,lija->ia  ', np.einsum('kjcd,klcd->jl  ', l2, t2), np.einsum('liba,jb->lija', mycc.w_oovv, t1)) * .5
    l1new += np.einsum('il,la->ia    ', np.einsum('kicd,klcd->il  ', l2, t2), np.einsum('ljba,jb->la  ', mycc.w_oovv, t1)) * .5
    l1new += np.einsum('jikl,klja->ia', np.einsum('jicd,klcd->jikl', l2, t2), np.einsum('klba,jb->klja', mycc.w_oovv, t1)) * .25
    l1new -= np.einsum('bd,bida->ia  ', np.einsum('klcb,klcd->bd', l2, t2), np.einsum('jida,jb->bida', mycc.w_oovv, t1)) * .5
    l1new += np.einsum('ad,id->ia    ', np.einsum('klca,klcd->ad', l2, t2), np.einsum('jidb,jb->id  ', mycc.w_oovv, t1)) * .5
    l1new -= np.einsum('kicj,jakc->ia', np.einsum('kicb,jb->kicj', l2, t1), np.einsum('ljda,klcd->jakc', mycc.w_oovv, t2))
    l1new -= np.einsum('kbca,ibkc->ia', np.einsum('kjca,jb->kbca', l2, t1), np.einsum('lidb,klcd->ibkc', mycc.w_oovv, t2))
    l1new += np.einsum('iald,ld->ia  ', np.einsum('kica,klcd->iald', l2, t2), np.einsum('ljdb,jb->ld', mycc.w_oovv, t1))
    l1new += np.einsum('bica,bc->ia  ', np.einsum('jica,jb->bica', l2, t1), np.einsum('kldb,klcd->bc', mycc.w_oovv, t2)) * .5
    l1new += np.einsum('klja,jikl->ia', np.einsum('klba,jb->klja', l2, t1), np.einsum('jicd,klcd->jikl', mycc.w_oovv, t2)) * .25
    l1new += np.einsum('kija,jk  ->ia', np.einsum('kiba,jb->kija', l2, t1), np.einsum('ljcd,klcd->jk  ', mycc.w_oovv, t2)) * .5
    l1new += np.einsum('jilk,lkja->ia', np.einsum('jidc,ld,kc->jilk', l2, t1, t1), np.einsum('lkba,jb->lkja', mycc.w_oovv, t1)) * .5
    l1new += np.einsum('kjla,likj->ia', np.einsum('kjda,ld->kjla', l2, t1), np.einsum('licb,kc,jb->likj', mycc.w_oovv, t1, t1)) * .5
    l1new -= np.einsum('kila,lk  ->ia', np.einsum('kida,ld->kila', l2, t1), np.einsum('ljcb,kc,jb->lk', mycc.w_oovv, t1, t1))

    def Pij(v2):
        return v2 - v2.transpose(1,0,2,3)
    def Pab(v2):
        return v2 - v2.transpose(0,1,3,2)
    def Pijab(v2):
        return Pij(Pab(v2))
    Pabij = Pijab

    l2new  =       mycc.w_oovv.copy()
    l2new += Pijab(np.einsum('ia,jb->ijab', l1, mycc.f_ov))
    l2new += Pijab(np.einsum('ia,kjcb,kc->ijab', l1, mycc.w_oovv, t1))
    l2new += Pij  (np.einsum('ic,cjab->ijab', l1, mycc.w_vovv))
    l2new -= Pab  (np.einsum('ka,ijkb->ijab', l1, mycc.w_ooov))
    l2new -= Pij  (np.einsum('ic,kc,kjab->ijab', l1, t1, mycc.w_oovv))
    l2new -= Pab  (np.einsum('ka,kc,ijcb->ijab', l1, t1, mycc.w_oovv))
    l2new += Pij  (np.einsum('kiab,jk->ijab', l2, mycc.f_oo))
    l2new -= Pab  (np.einsum('ijca,cb->ijab', l2, mycc.f_vv))
    l2new += np.einsum('ijcd,cdab->ijab', l2, mycc.w_vvvv) * .5
    l2new += np.einsum('klab,ijkl->ijab', l2, mycc.w_oooo) * .5
    l2new += Pabij(np.einsum('kica,jcbk->ijab', l2, mycc.w_ovvo))
    l2new += Pab  (np.einsum('ijca,kb,kc->ijab', l2, mycc.f_ov, t1))
    l2new += Pij  (np.einsum('kiab,jc,kc->ijab', l2, mycc.f_ov, t1))
    l2new -=      (np.einsum('ijdc,dcab->ijab', l2, np.einsum('dkab,kc->dcab', mycc.w_vovv, t1)))
    l2new += Pabij(np.einsum('kida,djkb->ijab', l2, np.einsum('djcb,kc->djkb', mycc.w_vovv, t1)))
    l2new += Pab  (np.einsum('ijda,db  ->ijab', l2, np.einsum('dkcb,kc->db  ', mycc.w_vovv, t1)))
    l2new -= Pabij(np.einsum('lica,cjlb->ijab', l2, np.einsum('kjlb,kc->cjlb', mycc.w_ooov, t1)))
    l2new +=      (np.einsum('lkab,ijlk->ijab', l2, np.einsum('ijlc,kc->ijlk', mycc.w_ooov, t1)))
    l2new -= Pij  (np.einsum('liab,jl  ->ijab', l2, np.einsum('kjlc,kc->jl  ', mycc.w_ooov, t1)))
    l2new -= Pij  (np.einsum('il  ,ljab->ijab', np.einsum('kicd,klcd->il  ', l2, t2), mycc.w_oovv)) * .5
    l2new +=      (np.einsum('ijkl,klab->ijab', np.einsum('ijcd,klcd->ijkl', l2, t2), mycc.w_oovv)) * .25
    l2new -= Pab  (np.einsum('ad  ,ijdb->ijab', np.einsum('klca,klcd->ad  ', l2, t2), mycc.w_oovv)) * .5
    l2new += Pabij(np.einsum('iald,ljdb->ijab', np.einsum('kica,klcd->iald', l2, t2), mycc.w_oovv))
    l2new -= Pab  (np.einsum('ijca,bc->ijab', l2, np.einsum('kldb,klcd->bc', mycc.w_oovv, t2))) * .5
    l2new +=      (np.einsum('klab,ijkl->ijab', l2, np.einsum('ijcd,klcd->ijkl', mycc.w_oovv, t2))) * .25
    l2new -= Pij  (np.einsum('kiab,jk  ->ijab', l2, np.einsum('ljcd,klcd->jk  ', mycc.w_oovv, t2))) * .5
    l2new +=      (np.einsum('ijlk,lkab->ijab', np.einsum('ijdc,ld,kc->ijlk', l2, t1, t1), mycc.w_oovv)) * .5
    l2new -= Pabij(np.einsum('kida,djkb->ijab', l2, np.einsum('ljcb,ld,kc->djkb', mycc.w_oovv, t1, t1)))
    l2new -= Pab  (np.einsum('ijda,db  ->ijab', l2, np.einsum('lkcb,kc,ld->db', mycc.w_oovv, t1, t1)))
    l2new +=      (np.einsum('lkab,ijlk->ijab', l2, np.einsum('ijdc,ld,kc->ijlk', mycc.w_oovv, t1, t1))) * .5
    l2new -= Pij  (np.einsum('liab,jl  ->ijab', l2, np.einsum('kjdc,ld,kc->jl', mycc.w_oovv, t1, t1)))

    eia = mycc.f_oo.diagonal()[:,None] - mycc.f_vv.diagonal()
    l1new = l1 + l1new / eia
    eijab = lib.direct_sum('ia+jb->ijab', eia, eia)
    l2new = l2 + l2new / eijab
    return l1new, l2new

def update_l1l2(mf, t1, t2, l1, l2, orbspin):
    mol = mf.mol
    nao,nmo = mf.mo_coeff[0].shape
    nelec = mol.nelectron
    nso = nmo * 2
    hcore = mf.get_hcore()
    h1e = np.zeros((nso,nso))
    idxa = orbspin == 0
    idxb = orbspin == 1
    idxaa = idxa[:,None]&idxa
    idxbb = idxb[:,None]&idxb
    h1e[idxaa] = reduce(np.dot, (mf.mo_coeff[0].T, hcore, mf.mo_coeff[0])).ravel()
    h1e[idxbb] = reduce(np.dot, (mf.mo_coeff[1].T, hcore, mf.mo_coeff[1])).ravel()
    int2e = np.zeros((nso,nso,nso,nso))
    int2e[idxaa[:,:,None,None]&idxaa] = ao2mo.full(mol, mf.mo_coeff[0], aosym='s1').ravel()
    int2e[idxbb[:,:,None,None]&idxbb] = ao2mo.full(mol, mf.mo_coeff[1], aosym='s1').ravel()
    eri_aabb = ao2mo.general(mol, [mf.mo_coeff[0],mf.mo_coeff[0],
                                   mf.mo_coeff[1],mf.mo_coeff[1]], aosym='s1').reshape([nmo]*4)
    int2e[idxaa[:,:,None,None]&idxbb] = eri_aabb.ravel()
    int2e[idxbb[:,:,None,None]&idxaa] = eri_aabb.transpose(2,3,0,1).ravel()
    int2e = int2e.transpose(0,2,1,3)
    int2e = int2e - int2e.transpose(0,1,3,2)
    mycc = ccsd(nso,nelec,h1e,int2e,h1e_is_fock=False)
    l1, l2 = update_l1l2_sub(mycc, t1, t2, l1, l2)

    return l1, l2


class KnownValues(unittest.TestCase):
    def test_update_amps(self):
        mf = scf.UHF(mol).run()
        numpy.random.seed(21)
        mf.mo_coeff = [numpy.random.random(mf.mo_coeff[0].shape)*.1] * 2
        mycc = uccsd.UCCSD(mf)
        eris = mycc.ao2mo()

        nocc = mol.nelectron // 2
        nvir = mol.nao_nr() - nocc
        numpy.random.seed(1)

        t1r = numpy.random.random((nocc,nvir))*.1
        t2r = numpy.random.random((nocc,nocc,nvir,nvir))*.1
        t2r = t2r + t2r.transpose(1,0,3,2)
        t1 = addons.spatial2spin(t1r)
        t2 = addons.spatial2spin(t2r)
        l1r = numpy.random.random((nocc,nvir))*.1
        l2r = numpy.random.random((nocc,nocc,nvir,nvir))*.1
        l2r = l2r + l2r.transpose(1,0,3,2)
        l1 = addons.spatial2spin(l1r)
        l2 = addons.spatial2spin(l2r)
        l1ref, l2ref = update_l1l2(mf, t1, t2, l1, l2, eris.orbspin)

        eris = uccsd_lambda._eris_spatial2spin(mycc, eris)
        imds = uccsd_lambda.make_intermediates(mycc, t1, t2, eris)
        l1, l2 = uccsd_lambda.update_amps(mycc, t1, t2, l1, l2, eris, imds)
        self.assertAlmostEqual(abs(l1-l1ref).max(), 0, 8)
        self.assertAlmostEqual(abs(l2-l2ref).max(), 0, 8)


if __name__ == "__main__":
    print("Full Tests for UCCSD lambda")
    unittest.main()
