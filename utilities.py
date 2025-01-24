# src/utilities.py

def rank2mmr(rank, immortal = None):
    """
    convert rank_tier to approximate mmr

    param rank rank_tier from opendota
    param immortal return value when medal is immortal and above
    return approximate mmr
    """
    if rank == None:
        return 0
    if rank >= 80:
        return immortal
    mmrm = [10, 770, 1540, 2310, 3080, 3850, 4620, 5630]
    medal = (rank // 10 - 1)
    mmr = mmrm[medal]
    mmr += (mmrm[medal + 1] - mmrm[medal]) * ((((rank % 10) - 1) / 5) + 0.1)
    return mmr
